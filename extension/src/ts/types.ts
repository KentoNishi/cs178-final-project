export enum Sender {
  System = "system",
  User = "user",
}

export interface Message {
  tokens: string[];
  sender: Sender;
}
