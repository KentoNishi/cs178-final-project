import { chatMessages, chatUserMessageInputListeners } from "../ts/stores";
import { Sender, type ChatInputCallback } from "../ts/types";

export const addUserInputListener = (callback: ChatInputCallback) => {
  chatUserMessageInputListeners.update((listeners) => [...listeners, callback]);
}

export const removeUserInputListener = (callback: ChatInputCallback) => {
  chatUserMessageInputListeners.update((listeners) => listeners.filter((listener) => listener !== callback));
}

export const dispatchUserInput = (message: string) => {
  chatMessages.update((messages) => [...messages, {
    tokens: [message],
    sender: Sender.User,
  }]);
  chatUserMessageInputListeners.update((listeners) => {
    listeners.forEach((listener) => listener(message));
    return listeners;
  });
}

export const initializeNewSystemMessage = (message: string) => {
  chatMessages.update((messages) => [...messages, {
    tokens: [],
    sender: Sender.System,
  }]);
}

export const appendToMostRecentSystemMessage = (message: string) => {
  chatMessages.update((messages) => {
    let lastMessage = messages[messages.length - 1];
    if (lastMessage.sender === Sender.System) {
      lastMessage = {
        ...lastMessage,
        tokens: [...lastMessage.tokens, message],
      };
    }
    return [...messages.slice(0, -1), lastMessage];
  });
}
