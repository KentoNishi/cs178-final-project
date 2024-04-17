import { writable } from 'svelte/store';
import { Sender, type ChatInputCallback, type Message } from './types';

export let chatPanelOpen = writable(false);
export let chatMessages = writable([{
  tokens: ['Welcome to the my.harvard ChatGPT assistant! How can I assist you today?'],
  sender: Sender.System
}] as Message[]);
export let chatUserMessageInputListeners = writable([] as ChatInputCallback[]);
