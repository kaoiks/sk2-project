#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>
#include <error.h>
#include <netdb.h>
#include <sys/epoll.h>
#include <unordered_set>
#include <list> 
#include <signal.h>
#include <iostream>
#include "json.hpp"
#include <chrono> 
#include <thread>
#include <unistd.h>
#include <fstream>
#include <algorithm>
#include <iterator>
#include <cstdlib>

using json = nlohmann::json;


class Client;

int servFd;
int epollFd;
std::unordered_set<Client*> clients;

std::vector<std::string> playersInGame;
json gameRanking;
bool counter = false;
bool inGame = false;

void ctrl_c(int);

int MIN_PLAYERS = 2;
void sendToAllBut(int fd, char * buffer, int count);
void sendTo(int fd, const char * buffer, int count);

void setPlayerUsername(int fd, std::string username);
void sendToAllGameStarted();
std::vector<std::string> playersNames();
int countPlayers();
void sendToAllGameStart();
void sendToAllLobby();
void gameLoop();
void sendToPlayersRoundInfo(int round, std::string word, std::vector<std::string> playersInGame);
bool playGame = true;
std::string getRandomWord();
void newRanking();
void updateRanking(std::string username, int points);
int guessedInCurrentRound = 0;
int notGuessedInCurrentRound = 0;
uint16_t readPort(char * txt);

void setReuseAddr(int sock);

struct Handler {
    virtual ~Handler(){}
    virtual void handleEvent(uint32_t events) = 0;
};


class Game{
    std::string status = "";
    
    
};



class Client : public Handler {
    int _fd;
    
    struct Buffer {
        Buffer() {data = (char*) malloc(len);}
        Buffer(const char* srcData, ssize_t srcLen) : len(srcLen) {data = (char*) malloc(len); memcpy(data, srcData, len);}
        ~Buffer() {free(data);}
        Buffer(const Buffer&) = delete;
        void doube() {len*=2; data = (char*) realloc(data, len);}
        ssize_t remaining() {return len - pos;}
        char * dataPos() {return data + pos;}
        char * data;
        ssize_t len = 32;
        ssize_t pos = 0;
    };

    int points = 0;
    std::string _username;
    Buffer readBuffer;
    std::list<Buffer> dataToWrite;
    void waitForWrite(bool epollout) {
        epoll_event ee {EPOLLIN|EPOLLRDHUP|(epollout?EPOLLOUT:0), {.ptr=this}};
        epoll_ctl(epollFd, EPOLL_CTL_MOD, _fd, &ee);
    }
public:
    Client(int fd) : _fd(fd) {
        epoll_event ee {EPOLLIN|EPOLLRDHUP, {.ptr=this}};
        epoll_ctl(epollFd, EPOLL_CTL_ADD, _fd, &ee);
    }

    virtual ~Client(){
        epoll_ctl(epollFd, EPOLL_CTL_DEL, _fd, nullptr);
        shutdown(_fd, SHUT_RDWR);
        close(_fd);
    }

    int fd() const {return _fd;}

    void setUsername(std::string inputName){
        _username = inputName;
    }

    std::string username() const {return _username;}

    virtual void handleEvent(uint32_t events) override {
        if(events & EPOLLIN) {
            ssize_t count = read(_fd, readBuffer.dataPos(), readBuffer.remaining());
            

            if(count <= 0)
                events |= EPOLLERR;
            else {
                //std::cout << "HERE" << std::endl;
                readBuffer.pos += count;
                char * eol = (char*) memchr(readBuffer.data, '\n', readBuffer.pos);
                if(eol == nullptr) {
                    //std::cout<< "HEREE" <<std::endl;
                    if(0 == readBuffer.remaining())
                        readBuffer.doube();
                } else {
                    do {
                        auto thismsglen = eol - readBuffer.data + 1;
                        
                        //sendToAllBut(_fd, readBuffer.data, thismsglen);
                        auto nextmsgslen =  readBuffer.pos - thismsglen;
                        memmove(readBuffer.data, eol+1, nextmsgslen);
                        readBuffer.pos = nextmsgslen;
                    } while((eol = (char*) memchr(readBuffer.data, '\n', readBuffer.pos)));
                    //*eol = '\0';
                    for(size_t i=0; i< strlen(readBuffer.data);++i ){
                        if (readBuffer.data[i] == '\n'){
                            readBuffer.data[i] = '\0';
                            break;
                        }
                    }
                    try{
                        std::string messageData(readBuffer.data, strlen(readBuffer.data));
                        std::cout<< messageData <<std::endl;
                        //string without \n at the end
                        
                        std::string message =  messageData.substr(0,messageData.length());
                        json data = json::parse(message);
                        std::string operationType = data["operation"].get<std::string>();

                        if (operationType == "SET_NAME"){
                            
                            std::string userNickname = data["username"].get<std::string>();
                            auto it = clients.begin();
                            bool exists = false;
                            while(it!=clients.end()){
                                Client * client = *it;
                                it++;
                                if(client->username() == userNickname){
                                    //client->write(buffer, count);
                                    exists = true;
                                    break;
                                }
                            }
                            
                            if (exists){
                                std::string response = "{\"response\":0}";
                                sendTo(_fd, response.c_str(), response.size());
                                std::cout<< "Username can't be accepted" <<std::endl;
                            }
                            else{

                                setPlayerUsername(_fd, userNickname);
                                std::string response = "{\"response\":1}";
                                sendTo(_fd, response.c_str(), response.size());
                                std::cout<< "Username accepted" <<std::endl;
                            }
                            if (inGame && gameRanking[userNickname] == nullptr){
                                std::cout<< "PLAYER JOINING EXISTING GAME" <<std::endl;
                                gameRanking[userNickname] = 0;
                                playersInGame.push_back(userNickname);
                            }
                            else if(inGame) {
                                std::cout<< "PLAYER REJOINED THE GAME" <<std::endl;
                            }
                        }
                        else if (operationType == "GUESSED"){
                            std::string nickname = data["username"].get<std::string>();
                            ++guessedInCurrentRound;
                            std::cout<< "GUESSED"<< std::endl;
                            updateRanking(nickname, countPlayers() - guessedInCurrentRound);
                        }
                        else if (operationType == "NOT_GUESSED"){
                            ++notGuessedInCurrentRound;
                            
                        }
                    }
                    catch(...){

                    }

                    //sendTo
                }
            }
        }
        if(events & EPOLLOUT) {
            do {
                
                int remaining = dataToWrite.front().remaining();
                int sent = send(_fd, dataToWrite.front().data+dataToWrite.front().pos, remaining, MSG_DONTWAIT);
                if(sent == remaining) {
                    dataToWrite.pop_front();
                    if(0 == dataToWrite.size()) {
                        waitForWrite(false);
                        break;
                    }
                    continue;
                } else if(sent == -1) {
                    if(errno != EWOULDBLOCK && errno != EAGAIN)
                        events |= EPOLLERR;
                } else
                    dataToWrite.front().pos += sent;
            } while(false);
        }
        if(events & ~(EPOLLIN|EPOLLOUT)) {
            remove();
        }
    }

    void write(const char * buffer, int count) {
        if(dataToWrite.size() != 0) {
            dataToWrite.emplace_back(buffer, count);
            return;
        }
        int sent = send(_fd, buffer, count, MSG_DONTWAIT);
        if(sent == count)
            return;
        if(sent == -1) {
            if(errno != EWOULDBLOCK && errno != EAGAIN){
                remove();
                return;
            }
            dataToWrite.emplace_back(buffer, count);
        } else {
            dataToWrite.emplace_back(buffer+sent, count-sent);
        }
        waitForWrite(true);
    }
    void remove() {
        printf("removing %d\n", _fd);
        clients.erase(this);
        delete this;
    }
};

class : public Handler {
    public:
    virtual void handleEvent(uint32_t events) override {
        if(events & EPOLLIN){
            sockaddr_in clientAddr{};
            socklen_t clientAddrSize = sizeof(clientAddr);
            
            auto clientFd = accept(servFd, (sockaddr*) &clientAddr, &clientAddrSize);
            if(clientFd == -1) error(1, errno, "accept failed");
            
            printf("new connection from: %s:%hu (fd: %d)\n", inet_ntoa(clientAddr.sin_addr), ntohs(clientAddr.sin_port), clientFd);
            
            clients.insert(new Client(clientFd));
        }
        if(events & ~EPOLLIN){
            error(0, errno, "Event %x on server socket", events);
            ctrl_c(SIGINT);
        }
    }
} servHandler;

int main(int argc, char ** argv){
    if(argc != 2) error(1, 0, "Need 1 arg (port)");
    auto port = readPort(argv[1]);
    srand(time(0));
    servFd = socket(AF_INET, SOCK_STREAM, 0);
    if(servFd == -1) error(1, errno, "socket failed");
    
    signal(SIGINT, ctrl_c);
    signal(SIGPIPE, SIG_IGN);
    
    setReuseAddr(servFd);
    
    sockaddr_in serverAddr{.sin_family=AF_INET, .sin_port=htons((short)port), .sin_addr={INADDR_ANY}};
    int res = bind(servFd, (sockaddr*) &serverAddr, sizeof(serverAddr));
    if(res) error(1, errno, "bind failed");
    
    res = listen(servFd, 1);
    if(res) error(1, errno, "listen failed");

    epollFd = epoll_create1(0);
    
    epoll_event ee {EPOLLIN, {.ptr=&servHandler}};
    epoll_ctl(epollFd, EPOLL_CTL_ADD, servFd, &ee);
    std::thread t1(gameLoop);
    while(true){
        try{
            if(-1 == epoll_wait(epollFd, &ee, 1, -1) && errno!=EINTR) {
                
                error(0,errno,"epoll_wait failed");
                ctrl_c(SIGINT);
                playGame = false;
            }
            
            

            ((Handler*)ee.data.ptr)->handleEvent(ee.events);
        }
        catch(...){
            
        }
    }  
    playGame = false;
    t1.join();
}


void gameLoop(){
    auto start = std::chrono::steady_clock::now();
    auto game_status_timer = std::chrono::steady_clock::now();
    while(true){
        
        if (countPlayers() >= MIN_PLAYERS){
                if (!counter && !inGame){
                    start = std::chrono::steady_clock::now();
                    std::cout<< "Starting game in 10 seconds"<<std::endl;
                    counter = true;
                    usleep(500000);
                    sendToAllGameStart();
                    continue;
                }
                else if(counter && !inGame){
                    if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - start).count() > 5000){
                        std::cout<< "Game has been started"<<std::endl;
                        inGame = true;
                        counter = false;
                    }
                    continue;
                }
                else if(inGame){
                    
                    std::cout<< "IN GAME"<<std::endl;
                    sendToAllGameStarted();
                    std::string word = getRandomWord();
                    std::transform(word.begin(), word.end(), word.begin(), ::toupper);
                    std::cout<< word <<std::endl;
                    playersInGame.clear();
                    std::vector<std::string> getNames = playersNames();
                    std::copy(getNames.begin(), getNames.end(), std::back_inserter(playersInGame));
                    newRanking();
                    
                    int round = 1;
                    guessedInCurrentRound = 0;
                    notGuessedInCurrentRound = 0;
                    sendToPlayersRoundInfo(round, word, playersInGame);
                    auto round_timer = std::chrono::steady_clock::now();
                    while(true){
                        if (countPlayers() < MIN_PLAYERS){
                            counter = false;
                            inGame = false;
                            std::cout<< "GETTING BACK TO LOBBY"<<std::endl;
                            sendToAllLobby();
                            break;
                        }
                        else{
                            if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - round_timer).count() > 45000 || countPlayers() == (guessedInCurrentRound + notGuessedInCurrentRound)){
                                if (round < 5){
                                    std::cout << "ROUND END" <<std::endl;
                                    ++round;
                                    word = getRandomWord();
                                    std::transform(word.begin(), word.end(), word.begin(), ::toupper);
                                    guessedInCurrentRound = 0;
                                    notGuessedInCurrentRound = 0;
                                    sendToPlayersRoundInfo(round, word, playersInGame);
                                    round_timer = std::chrono::steady_clock::now();
                                }
                                else{
                                    counter = false;
                                    inGame = false;
                                    std::cout<< "BACK TO LOBBY"<<std::endl;
                                    break;
                                }
                                }
                            }
                    }
                }

        if (countPlayers() < MIN_PLAYERS){
            if (inGame){
                counter = false;
                inGame = false;
                std::cout<< "BACK TO LOBBY"<<std::endl;
            }
            else{
                guessedInCurrentRound = 0;
                if (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - game_status_timer).count() > 5000){
                        std::cout<< "STILL LOBBY"<<std::endl;
                        //sendToAllLobby();
                        game_status_timer = std::chrono::steady_clock::now();
                    }
            }

        }
    }
    
}

}

void newRanking(){
    gameRanking.clear();
    for(std::string player : playersInGame ){
        gameRanking[player] = 0;
    }
}

void updateRanking(std::string username, int points){
    gameRanking[username] = gameRanking[username].get<int>() + points;
    std::cout<< gameRanking.dump() << std::endl;
}

std::vector<std::string> playersNames(){
    std::vector<std::string> playersInGame;
    auto it = clients.begin();
    while(it!=clients.end()){
        Client * client = *it;
        it++;
        playersInGame.push_back(client->username());
    }
    return playersInGame;
}


uint16_t readPort(char * txt){
    char * ptr;
    auto port = strtol(txt, &ptr, 10);
    if(*ptr!=0 || port<1 || (port>((1<<16)-1))) error(1, 0, "illegal argument %s", txt);
    return port;
}

void setReuseAddr(int sock){
    const int one = 1;
    int res = setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one));
    if(res) error(1,errno, "setsockopt failed");
}

void ctrl_c(int){
    for(Client * client : clients)
        delete client;
    close(servFd);
    printf("Closing server\n");
    exit(0);
}

void sendToAllBut(int fd, char * buffer, int count){
    auto it = clients.begin();
    while(it!=clients.end()){
        Client * client = *it;
        it++;
        if(client->fd()!=fd)
            client->write(buffer, count);
    }
}

int countPlayers(){
    auto it = clients.begin();
    int counter = 0;
    while(it!=clients.end()){
        Client * client = *it;
        it++;
        if(client->username().empty()){
        }
        else{
            ++counter;
        }  
    }
    return counter;
}


void sendTo(int fd, const char * buffer, int count){
    auto it = clients.begin();
    while(it!=clients.end()){
        Client * client = *it;
        it++;
        if(client->fd() == fd)
            client->write(buffer, count);
    }
}

void setPlayerUsername(int fd, std::string username){
    auto it = clients.begin();
    while(it!=clients.end()){
        Client * client = *it;
        it++;
        if(client->fd() == fd){
            client->setUsername(username);
        }
    }
}

void sendToAllGameStart(){
    std::string payload = "{\"message\":\"10_SECOND_ALERT\"}\n";

    auto it = clients.begin();
    while(it!=clients.end()){
        Client * client = *it;
        it++;
        client->write(payload.c_str(), payload.size());
    }
}

void sendToAllGameStarted(){
    std::string payload = "{\"message\":\"IN_GAME\"}\n";

    auto it = clients.begin();
    while(it!=clients.end()){
        Client * client = *it;
        it++;
        client->write(payload.c_str(), payload.size());
    }
}

void sendToAllLobby(){
    std::string payload = "{\"message\":\"IN_LOBBY\"}\n";
    //std::cout << "STILL IN LOBBY" << std::endl;
    auto it = clients.begin();
    while(it!=clients.end()){
        Client * client = *it;
        it++;
        client->write(payload.c_str(), payload.size());
    }
}

void sendToPlayersRoundInfo(int round, std::string word,std::vector<std::string> playersInGame){
    json payload;
    payload["message"] = "GAME_STATUS";
    payload["round"] = round;
    word.pop_back();
    payload["word"] = word;
    payload["ranking"] = gameRanking;
    
    std::string payload_string = payload.dump() + "\n"; 
    auto it = clients.begin();
    while(it!=clients.end()){
        Client * client = *it;
        it++;
        
        if (std::find(playersInGame.begin(), playersInGame.end(), client->username()) != playersInGame.end()) {
            client->write(payload_string.c_str(), payload_string.size());
        }
        else{

        }
    }   
}


std::string getRandomWord(){
    std::vector<std::string> words;
    std::ifstream file("words.txt");
    for (std::string line; std::getline(file, line); words.push_back(line)) {}
    int random = std::rand() % words.size();
    std::string selected_word = words[random];
    return selected_word;
}
