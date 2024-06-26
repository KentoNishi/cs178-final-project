import { writable } from 'svelte/store';
import { BackendState, Sender, type ChatInputCallback, type Message } from './types';
import welcome from '../assets/welcome.md?raw';

export let chatPanelOpen = writable(false);
export let chatMessages = writable([] as Message[]);
export let chatUserMessageInputListeners = writable([] as ChatInputCallback[]);
export let backendState = writable(BackendState.Default);