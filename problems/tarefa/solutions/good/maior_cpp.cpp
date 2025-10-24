// OBI2022
// Tarefa Maior

#include<bits/stdc++.h>

using namespace std;

int N, M, S;

int main (void) {
    scanf ("%d%d%d", &N, &M, &S);

    bool achou = false;
    int resp;
		
    for (int i=M; i>N; i--) {
      int soma = 0;
      int x = i;
      while (x > 0) {
	soma += x % 10;
	x /= 10;
      }
      if (soma == S) {
	achou = true;
	resp = i;
	break;
      }
    }	    
    
    if (achou)
      printf("%d\n", resp);
    else
      printf("-1\n");


    return 0;
}
