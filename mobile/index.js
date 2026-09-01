import { registerRootComponent } from 'expo';
import App from './App';
import { initCrashReporter } from './src/services/crashReporter';

initCrashReporter();
registerRootComponent(App);