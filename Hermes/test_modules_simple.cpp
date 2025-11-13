/**
 * 简化的模块化性能测试程序
 * 只测试核心密码学操作，不依赖 ZeroMQ
 */

#include <iostream>
#include <vector>
#include <chrono>
#include <time.h>
#include <sys/time.h>
#include <openssl/sha.h>
#include <emp-tool/emp-tool.h>
#include <emp-agmpc/emp-agmpc.h>
#include "gmp.h"
#include "include/pbc.h"
#include "include/pbc_test.h"
#include "include/utils.h"
#include "config.hpp"
#include "types.hpp"

using namespace std;
using namespace emp;

// 全局变量（从 hickae.hpp 复制）
mpz_t           q;
mpz_t           p;
pairing_t       pairing;
gmp_randstate_t random_state;
uint8_t         rd_data[256];
mpz_t           alpha;
element_t       g1;
element_t       g2;
element_t       gt;

HICKAE_PrvKey   sk;
HICKAE_PubKey   pk;
element_t       *public_parameters;
mpz_t           *sigma_hat;
mpz_t           *sigma_prime;
mpz_t           *sigma_class;
element_t       *class_binding_key;
element_t       **correlation;

PRG prg;

// 计时函数
auto clock_start() {
    return chrono::high_resolution_clock::now();
}

double time_from(chrono::high_resolution_clock::time_point start) {
    auto end = chrono::high_resolution_clock::now();
    return chrono::duration_cast<chrono::microseconds>(end - start).count();
}

// 包含 HICKAE 函数实现
#include "hickae.hpp"

int main(int argc, char* argv[]) {
    int num_writers = 5;
    int num_iterations = 50;
    
    if (argc > 1) num_writers = atoi(argv[1]);
    if (argc > 2) num_iterations = atoi(argv[2]);
    
    cout << "========================================" << endl;
    cout << "  HICKAE 模块化性能测试" << endl;
    cout << "========================================" << endl;
    cout << "写者数量: " << num_writers << endl;
    cout << "测试迭代: " << num_iterations << " 次" << endl;
    cout << "========================================" << endl << endl;
    
    // 1. Setup
    cout << "[1/6] HICKAE_Setup..." << endl;
    auto start = clock_start();
    HICKAE_Setup(num_writers);
    double setup_time = time_from(start);
    cout << "  Setup: " << setup_time / 1000.0 << " ms" << endl << endl;
    
    // 2. KeyGen
    cout << "[2/6] HICKAE_KeyGen..." << endl;
    start = clock_start();
    HICKAE_KeyGen();
    double keygen_time = time_from(start);
    cout << "  KeyGen: " << keygen_time / 1000.0 << " ms" << endl << endl;
    
    // 3. IGen
    cout << "[3/6] HICKAE_IGen..." << endl;
    start = clock_start();
    HICKAE_IGen(num_writers);
    double igen_time = time_from(start);
    cout << "  IGen: " << igen_time / 1000.0 << " ms" << endl << endl;
    
    // 4. Prep
    cout << "[4/6] HICKAE_Prep..." << endl;
    start = clock_start();
    HICKAE_Prep(num_writers);
    double prep_time = time_from(start);
    cout << "  Prep: " << prep_time / 1000.0 << " ms" << endl << endl;
    
    // 5. Encrypt
    cout << "[5/6] HICKAE_Encrypt (批量 " << num_iterations << " 次)..." << endl;
    double total_encrypt = 0;
    for (int i = 0; i < num_iterations; i++) {
        PEKS_Token token;
        unsigned char msg[32];
        sprintf((char*)msg, "test_%d", i);
        
        start = clock_start();
        HICKAE_Encrypt(0, (char*)"keyword", msg, &token);
        total_encrypt += time_from(start);
    }
    double avg_encrypt = total_encrypt / num_iterations;
    cout << "  平均: " << avg_encrypt << " μs/次" << endl << endl;
    
    // 6. Extract
    cout << "[6/6] HICKAE_Extract (批量 " << num_iterations << " 次)..." << endl;
    vector<int> writers;
    for (int i = 0; i < num_writers; i++) writers.push_back(i);
    
    double total_extract = 0;
    for (int i = 0; i < num_iterations; i++) {
        PEKS_AggKey key;
        char kw[32];
        sprintf(kw, "kw_%d", i);
        
        start = clock_start();
        HICKAE_Extract(writers, kw, &key);
        total_extract += time_from(start);
    }
    double avg_extract = total_extract / num_iterations;
    cout << "  平均: " << avg_extract << " μs/次" << endl << endl;
    
    // 总结
    cout << "========================================" << endl;
    cout << "  性能总结" << endl;
    cout << "========================================" << endl;
    cout << "Setup:   " << setup_time / 1000.0 << endl;
    cout << "KeyGen:  " << keygen_time / 1000.0 << endl;
    cout << "IGen:    " << igen_time / 1000.0 << endl;
    cout << "Prep:    " << prep_time / 1000.0 << endl;
    cout << "Encrypt: " << avg_encrypt << endl;
    cout << "Extract: " << avg_extract << endl;
    cout << "========================================" << endl;
    
    return 0;
}

