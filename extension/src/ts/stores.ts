import { writable } from 'svelte/store';
import { Sender, type ChatInputCallback, type Message } from './types';
import welcome from '../assets/welcome.md?raw';

export let chatPanelOpen = writable(false);
export let chatMessages = writable([{
  tokens: [welcome],
  sender: Sender.System
}] as Message[]);
export let chatUserMessageInputListeners = writable([] as ChatInputCallback[]);
