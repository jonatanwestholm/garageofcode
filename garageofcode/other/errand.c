#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/queue.h>

#define FILENAME "/home/jdw/garageofcode/code/garageofcode/other/errand.txt"
#define MAX_LINE_SIZE 1024

struct entry {
   char line[MAX_LINE_SIZE];
   TAILQ_ENTRY(entry) entries;             /* Tail queue. */
};

TAILQ_HEAD(tailhead, entry);

void filecopy(FILE* ifp, FILE* ofp){
    int c;
    while((c = getc(ifp)) != EOF)
        putc(c, ofp);
}

void main(int argc, char** argv){
    FILE *fp;

    if(strcmp(argv[1], "push") == 0){
        fp = fopen(FILENAME, "a");
        printf("%s\n", argv[2]);
        char* line = argv[2];
        fputs(line, fp);
        fputs("\n", fp);
        fclose(fp);
    }
    else if(strcmp(argv[1], "list") == 0){
        fp = fopen(FILENAME, "r");
        filecopy(fp, stdout);
        fclose(fp);
    }else if(strcmp(argv[1], "rm") == 0){
        fp = fopen(FILENAME, "w");
        fprintf(fp, "");
        fclose(fp);
    }else if(strcmp(argv[1], "pop") == 0){
        fp = fopen(FILENAME, "r");
        int num_lines = 0;
        struct tailhead head;
        TAILQ_INIT(&head);
        char* line = calloc(MAX_LINE_SIZE, sizeof(char));
        while(fgets(line, MAX_LINE_SIZE, fp) != NULL){
            struct entry* e = calloc(1, sizeof(struct entry));
            strncpy(e->line, line, MAX_LINE_SIZE-1);
            TAILQ_INSERT_HEAD(&head, e, entries);            
        }
        struct entry* current = TAILQ_FIRST(&head);
        struct entry* temp;
        char input[1];
        int iter = 0;
        while(iter < 10){
            iter++;
            printf(" %s throwaway\n", current->line);
            char c = *fgets(input, 2, stdin);
            if(c == 'j'){
                temp = TAILQ_NEXT(current, entries);
                if(temp != NULL){
                    current = temp;
                }
            }else if(c == 'l'){
                temp = TAILQ_PREV(current, tailhead, entries);
                if(temp != NULL){
                    current = temp;
                }
            }else if(c == 'q'){
                break;
            }
        }
        /*
        */
        fclose(fp);
    }else{
        printf("Unknown command: %s\n", argv[1]);
    }
}