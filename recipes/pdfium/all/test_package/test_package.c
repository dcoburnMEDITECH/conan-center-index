#include <fpdfview.h>
#include <stdio.h>

int main(void) {
    FPDF_InitLibrary();
    printf("pdfium OK, last error: %lu\n", FPDF_GetLastError());
    FPDF_DestroyLibrary();
    return 0;
}
