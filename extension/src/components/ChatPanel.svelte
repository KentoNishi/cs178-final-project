<script lang="ts">
  import { chatMessages, chatPanelOpen } from '../ts/stores';
  // @ts-ignore
  import Moveable from 'svelte-moveable';
  import InnerChatInterface from './InnerChatInterface.svelte';
    import type { ArtifactContent } from '../ts/types';
  // import welcome from '../assets/welcome.md?raw';
  // import { Sender } from '../ts/types';
  let target: HTMLElement;
  const resizeCallback = ({ width, height }: { width: number; height: number }) => {
    target.style.width = `${width}px`;
    target.style.height = `${height}px`;
  };
  let updateRect: any;
  let artifact: ArtifactContent = {
    query_message     : "",
    prompts           : [],
    response_objects  : [],
    response_contents : [],
    references        : [],
    answer            : ""
  };

  const resetMessages = () => {
    $chatMessages = [];
  };
  const focus = () => (target.querySelector('input[type="text"]') as HTMLInputElement).focus();
  $: if ($chatPanelOpen) {
    artifact = {
      query_message     : "",
      prompts           : [],
      response_objects  : [],
      response_contents : [],
      references        : [],
      answer            : ""
    };
    focus();
  }
</script>

<svelte:window on:resize={updateRect} />

<div
  class="bottom-right"
  class:open={$chatPanelOpen}
  class:closed={!$chatPanelOpen}
  bind:this={target} style="width: 60%; height: 60%;"
>
  <InnerChatInterface bind:artifact />
  <button class="material-symbols-outlined close-button" on:click|preventDefault={() => {
    $chatPanelOpen = false;
    resetMessages();
   }}>delete_forever</button>
</div>
{#if $chatPanelOpen}
  <Moveable
    target={target}
    resizable
    onResize={resizeCallback}
    renderDirections={['nw']}
    edge
    className={$chatPanelOpen ? 'open' : 'closed'}
    origin={false}
    bind:updateRect
  />
{/if}

<style>
  .bottom-right {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.3s;
    background-color: white;
    min-width: 400px;
    min-height: 400px;
    box-shadow: 0 0 16px rgba(0, 0, 0, 0.25);
  }
  .open, :global(.open) {
    opacity: 1;
  }
  :global(.closed) {
    opacity: 0;
    pointer-events: none;
    touch-action: none;
  }
  .close-button {
    position: absolute;
    top: 0;
    right: 0;
    background-color: white;
    color: black;
    border: none;
    cursor: pointer;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    transform: translate(-3px, 2px);
    z-index: 1000;
  }
</style>
