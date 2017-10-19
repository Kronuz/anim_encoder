// [https://stackoverflow.com/questions/16952055/how-to-programatically-get-an-osx-window-id-from-a-process-id-on-10-6-using-ap]

#include <Carbon/Carbon.h>

// compile as such:
//  gcc -framework carbon -framework foundation -o GetWindowList GetWindowList.c

int main(int argc, char **argv) {

    CFArrayRef windowList;

    if (argc != 1) {
        printf("usage: %s\n", argv[0]);
        exit(1);
    }

    windowList = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements, kCGNullWindowID);
    NSLog(CFSTR("Array: %@"), windowList);
    CFRelease(windowList);

}
