export enum Sender {
  System = "system",
  User = "user",
}

export interface Message {
  tokens: string[];
  sender: Sender;
}

export type ChatInputCallback = (message: string) => void;
