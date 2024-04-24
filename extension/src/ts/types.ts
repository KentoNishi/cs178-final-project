export enum Sender {
  System = "system",
  User = "user",
}

export interface Message {
  tokens: string[];
  sender: Sender;
}

export type ChatInputCallback = (message: string) => void;
export enum BackendState {
  Generating = "generating",
  Default = "default",
  Error = "error",
};
