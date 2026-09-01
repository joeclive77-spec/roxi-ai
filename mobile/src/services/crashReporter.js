import { API_BASE_URL } from './config';

/**
 * Global JS error reporter. On any uncaught error (including launch-time
 * module-eval failures), POST the stack to the backend so it lands in
 * Render logs — release builds hide native logcat from adb/Termux, and
 * this is the only channel that reliably reaches us.
 */
export function initCrashReporter() {
  const send = (kind, err) => {
    try {
      fetch(`${API_BASE_URL}/api/crashlog`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          kind,
          message: err && err.message,
          stack: err && err.stack,
          app: 'roxi-ai-mobile',
          version: '0.1.0',
        }),
      }).catch(() => {});
    } catch (_e) {
      // Reporter failure must never loop back into a crash.
    }
  };

  if (global.ErrorUtils) {
    const orig = global.ErrorUtils.getGlobalHandler && global.ErrorUtils.getGlobalHandler();
    global.ErrorUtils.setGlobalHandler((err, isFatal) => {
      send('global', err);
      if (orig && typeof orig === 'function') orig(err, isFatal);
    });
  }
  if (global.HermesInternal) {
    try { global.HermesInternal.enableSampledCPUProfiler(); } catch (_e) {}
  }
}