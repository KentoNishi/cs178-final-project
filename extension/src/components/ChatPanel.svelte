<script lang="ts">
  import { chatPanelOpen } from '../ts/stores';
  // @ts-ignore
  import Moveable from 'svelte-moveable';
  import InnerChatInterface from './InnerChatInterface.svelte';
  let target: HTMLElement;
  const resizeCallback = ({ width, height }: { width: number; height: number }) => {
    target.style.width = `${width}px`;
    target.style.height = `${height}px`;
  };
</script>

<div class="bottom-right" class:open={$chatPanelOpen} bind:this={target} style="width: 50%; height: 50%;">
  <InnerChatInterface />
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
    min-width: 40 0px;
    min-height: 40  0px;
    box-shadow: 0 0 16px rgba(0, 0, 0, 0.25);
  }
  .open, :global(.open) {
    opacity: 1;
  }
  :global(.closed) {
    opacity: 0;
  }
</style>
