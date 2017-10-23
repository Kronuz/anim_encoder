// gcc -framework AppKit -o record record.m

#import <AppKit/AppKit.h>

const int64_t FRAME_DELAY = 1000000 / 24;

int64_t now() {
	struct timespec tms;
	clock_gettime(CLOCK_REALTIME, &tms);
	int64_t microseconds = tms.tv_sec * 1000000;
	microseconds += tms.tv_nsec / 1000;
	if (tms.tv_nsec % 1000 >= 500) {
		++microseconds;
	}
	return microseconds;
}

struct FullRep {
	int64_t time;
	NSBitmapImageRep *newRep;
};

int main(int argc, char **argv) {
	NSString *windowString = nil;
	const char* path;
	int windowID = 0;
	int seconds = 5;

	if (argc >= 2 && argc <= 4) {
		path = argv[1];
		windowID = atoi(argv[2]);
		if (argc == 4) {
			seconds = atoi(argv[3]);
		}

		CFArrayRef windowList = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements, kCGNullWindowID);
		for (NSDictionary *window in (NSMutableArray*)windowList) {
			NSString *name = [window objectForKey:@"kCGWindowName"];
			NSString *owner = [window objectForKey:@"kCGWindowOwnerName"];
			int pid = [[window objectForKey:@"kCGWindowOwnerPID"] intValue];
			int wid = [[window objectForKey:@"kCGWindowNumber"] intValue];
			if (wid && name && pid && owner && [name length]) {
				if (windowID == wid) {
					windowString = [NSString stringWithFormat:@"%d: %@ (pid:%d) -> %@", wid, owner, pid, name];
					break;
				}
			}
		}
		CFRelease(windowList);
	}

	if (!windowString) {
		fprintf(stderr, "usage: %s <output> <windowID> [seconds]\n", argv[0]);
        fprintf(stderr, "  windowid   window ID (see below)\n");
        fprintf(stderr, "  seconds    recording time\n");
        fprintf(stderr, "\n");
        fprintf(stderr, "Current windows:\n");
		CFArrayRef windowList = CGWindowListCopyWindowInfo(kCGWindowListExcludeDesktopElements, kCGNullWindowID);
		for (NSDictionary *window in (NSMutableArray*)windowList) {
			NSString *name = [window objectForKey:@"kCGWindowName"];
			NSString *owner = [window objectForKey:@"kCGWindowOwnerName"];
			int pid = [[window objectForKey:@"kCGWindowOwnerPID"] intValue];
			int wid = [[window objectForKey:@"kCGWindowNumber"] intValue];
			if (wid && name && pid && owner && [name length]) {
				windowString = [NSString stringWithFormat:@"%8d: %@ (pid:%d) -> %@", wid, owner, pid, name];
				fprintf(stderr, "%s\n", [windowString UTF8String]);
			}
		}
		CFRelease(windowList);
		exit(64);
	}

	int64_t start = now();
	int64_t stop = start + (1 * 10000000);

	int max_reps = (1 + seconds) * 24;
	struct FullRep reps[max_reps];
	int rep = 0;

	fprintf(stderr, "Starting Recording\n");
	fprintf(stderr, "==================\n");
	fprintf(stderr, "Recording window %s\n", [windowString UTF8String]);

	for (int wait = 5; wait >= 0; --wait) {
		fprintf(stderr, "For %d seconds, starting in %d seconds...\r", seconds, wait);
		sleep(1);
	}
	fprintf(stderr, "\a\033[2K\rRecording for %d seconds...\n", seconds);

	while (start < stop && rep < max_reps) {
		CGImageRef cgImage = CGWindowListCreateImage(
			CGRectNull,
			kCGWindowListOptionOnScreenAboveWindow | kCGWindowListOptionIncludingWindow | kCGWindowListExcludeDesktopElements,
			windowID,
			kCGWindowImageBoundsIgnoreFraming);
		reps[rep].time = start;
		reps[rep].newRep = [[[NSBitmapImageRep alloc] initWithCGImage:cgImage] autorelease];
		++rep;

		CFRelease(cgImage);

		int64_t end = now();
		int64_t sleep = FRAME_DELAY - (end - start);
		if (sleep > 0) {
			fprintf(stderr, ".");
			usleep(sleep);
			start = now();
		} else {
			fprintf(stderr, "!");
			start = end;
		}
	}

	fprintf(stderr, "\a\r");

	NSData *pngOldData = nil;
	for (int i = 0; i < rep; ++i) {
		NSString *filename = [NSString stringWithFormat:@"%s/screen_%lld.png", path, reps[i].time / 1000];
		// fprintf(stderr, "%s\n", [filename UTF8String]);
		NSData *pngData = [reps[i].newRep representationUsingType:NSPNGFileType properties:@{}];
		if (pngOldData == nil || ![pngData isEqualToData:pngOldData]) {
			[pngData writeToFile:filename atomically:YES];
			pngOldData = pngData;
			fprintf(stderr, "-");
		} else {
			fprintf(stderr, "=");
		}
	}
}
