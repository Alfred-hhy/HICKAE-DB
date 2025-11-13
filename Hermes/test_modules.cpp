/**
 * 模块化性能测试程序
 * 用于单独测试 HICKAE 各个组件的性能
 */

#include <iostream>
#include <vector>
#include <chrono>
#include "hickae.hpp"

using namespace std;

// 计时函数
auto clock_start() {
    return chrono::high_resolution_clock::now();
}

double time_from(chrono::high_resolution_clock::time_point start) {
    auto end = chrono::high_resolution_clock::now();
    return chrono::duration_cast<chrono::microseconds>(end - start).count();
}

int main(int argc, char* argv[]) {
    int num_writers = 5;  // 默认 5 个写者
    int num_iterations = 100;  // 测试迭代次数
    
    if (argc > 1) {
        num_writers = atoi(argv[1]);
    }
    if (argc > 2) {
        num_iterations = atoi(argv[2]);
    }
    
    cout << "========================================" << endl;
    cout << "  HICKAE 模块化性能测试" << endl;
    cout << "========================================" << endl;
    cout << "写者数量: " << num_writers << endl;
    cout << "测试迭代: " << num_iterations << " 次" << endl;
    cout << "========================================" << endl << endl;
    
    // ========================================
    // 1. 测试 HICKAE_Setup
    // ========================================
    cout << "[1/5] 测试 HICKAE_Setup..." << endl;
    auto start = clock_start();
    HICKAE_Setup(num_writers);
    double setup_time = time_from(start);
    cout << "  Setup 时间: " << setup_time / 1000.0 << " ms" << endl << endl;
    
    // ========================================
    // 2. 测试 HICKAE_KeyGen
    // ========================================
    cout << "[2/5] 测试 HICKAE_KeyGen..." << endl;
    start = clock_start();
    HICKAE_KeyGen();
    double keygen_time = time_from(start);
    cout << "  KeyGen 时间: " << keygen_time / 1000.0 << " ms" << endl << endl;
    
    // ========================================
    // 3. 测试 HICKAE_IGen
    // ========================================
    cout << "[3/5] 测试 HICKAE_IGen..." << endl;
    start = clock_start();
    HICKAE_IGen(num_writers);
    double igen_time = time_from(start);
    cout << "  IGen 时间: " << igen_time / 1000.0 << " ms" << endl << endl;
    
    // ========================================
    // 4. 测试 HICKAE_Prep
    // ========================================
    cout << "[4/5] 测试 HICKAE_Prep..." << endl;
    start = clock_start();
    HICKAE_Prep(num_writers);
    double prep_time = time_from(start);
    cout << "  Prep 时间: " << prep_time / 1000.0 << " ms" << endl << endl;
    
    // ========================================
    // 5. 测试 HICKAE_Encrypt (批量)
    // ========================================
    cout << "[5/5] 测试 HICKAE_Encrypt (批量 " << num_iterations << " 次)..." << endl;
    
    double total_encrypt_time = 0;
    for (int i = 0; i < num_iterations; i++) {
        PEKS_Token token;
        unsigned char msg[32];
        sprintf((char*)msg, "test_message_%d", i);
        
        start = clock_start();
        HICKAE_Encrypt(0, (char*)"keyword_test", msg, &token);
        total_encrypt_time += time_from(start);
    }
    
    double avg_encrypt_time = total_encrypt_time / num_iterations;
    cout << "  总时间: " << total_encrypt_time / 1000.0 << " ms" << endl;
    cout << "  平均时间: " << avg_encrypt_time << " μs/次" << endl;
    cout << "  吞吐量: " << (1000000.0 / avg_encrypt_time) << " 次/秒" << endl << endl;
    
    // ========================================
    // 6. 测试 HICKAE_Extract (批量)
    // ========================================
    cout << "[6/6] 测试 HICKAE_Extract (批量 " << num_iterations << " 次)..." << endl;
    
    vector<int> writer_subset;
    for (int i = 0; i < num_writers; i++) {
        writer_subset.push_back(i);
    }
    
    double total_extract_time = 0;
    for (int i = 0; i < num_iterations; i++) {
        PEKS_AggKey agg_key;
        char keyword[32];
        sprintf(keyword, "keyword_%d", i);
        
        start = clock_start();
        HICKAE_Extract(writer_subset, keyword, &agg_key);
        total_extract_time += time_from(start);
    }
    
    double avg_extract_time = total_extract_time / num_iterations;
    cout << "  总时间: " << total_extract_time / 1000.0 << " ms" << endl;
    cout << "  平均时间: " << avg_extract_time << " μs/次" << endl;
    cout << "  吞吐量: " << (1000000.0 / avg_extract_time) << " 次/秒" << endl << endl;
    
    // ========================================
    // 总结
    // ========================================
    cout << "========================================" << endl;
    cout << "  性能总结" << endl;
    cout << "========================================" << endl;
    cout << "Setup:   " << setup_time / 1000.0 << " ms" << endl;
    cout << "KeyGen:  " << keygen_time / 1000.0 << " ms" << endl;
    cout << "IGen:    " << igen_time / 1000.0 << " ms" << endl;
    cout << "Prep:    " << prep_time / 1000.0 << " ms" << endl;
    cout << "Encrypt: " << avg_encrypt_time << " μs/次" << endl;
    cout << "Extract: " << avg_extract_time << " μs/次" << endl;
    cout << "========================================" << endl;
    
    return 0;
}

