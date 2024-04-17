<script lang="ts">
  import { Sender, type Message } from '../ts/types';

  let messages: Message[] = [{
    tokens: ['Welcome to the my.harvard ChatGPT assistant! How can I assist you today?'],
    sender: Sender.System
  }];
</script>

<div class="split-wrapper">
  <div class="message-scroller">
    {#each messages as message, i}
      <div class="message" class:system={message.sender === Sender.System} class:user={message.sender === Sender.User}>
        {#if message.sender === Sender.System}
          <div class="system-message">{message.tokens.join(' ')}</div>
        {:else}
          <div class="user-message">{message.tokens.join(' ')}</div>
        {/if}
      </div>
    {/each}
  </div>
  <div class="message-input">
    <input type="text" class="textbox" placeholder="Type a message..." />
    <button class="material-symbols-outlined send-button">send</button>
  </div>
</div>

<style>
  .split-wrapper {
    display: grid;
    grid-template-rows: 1fr auto;
    flex-direction: column;
    height: 100%;
    padding: 12px;
  }

  .split-wrapper {
    height: 100%;
    overflow-y: auto;
  }

  .message {
    margin-bottom: 12px;
    display: flex;
    justify-content: flex-start;
    max-width: 80%;
  }

  .message>div {
    padding: 8px 12px;
    border-radius: 12px;
  }

  .system-message {
    background-color: var(--color-primary);
    color: white;
    float: left;
  }

  .user-message {
    background-color: #f0f0f0;
    color: black;
    float: right;
  }

  .message.user {
    justify-content: flex-end;
  }

  .message-input {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #b0b0b0;
    padding-top: 12px;
  }
  
  .textbox {
    flex: 1;
    padding: 8px;
    border-radius: 20px 0px 0px 20px;
    border-right: 0px !important;
    height: 40px;
  }
  
  .send-button {
    padding: 8px 12px;
    border-radius: 0px 20px 20px 0px;
    background-color: var(--color-primary);
    color: white;
    cursor: pointer;
    border-left: 0px !important;
    height: 40px;
    vertical-align: middle;
    text-align: center;
    padding: 5px 10px;
  }

  .textbox, .send-button {
    border-color: #b0b0b0;
    border-width: 1px;
    border-style: solid;
  }
</style>

