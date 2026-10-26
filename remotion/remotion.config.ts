/**
 * Note: When using the Node.JS APIs, the config file
 * doesn't apply. Instead, pass options directly to the APIs.
 *
 * All configuration options: https://remotion.dev/docs/config
 */

import { Config } from "@remotion/cli/config";
import { enableTailwind } from '@remotion/tailwind-v4';

Config.setRspack(true);
Config.setVideoImageFormat("jpeg");
// Sem isto o H.264 sai yuvj420p (full range, bt470bg); Reels/QA pedem yuv420p bt709.
Config.setColorSpace("bt709");
Config.setPixelFormat("yuv420p");
Config.setOverwriteOutput(true);
Config.overrideBundlerConfig(enableTailwind);
