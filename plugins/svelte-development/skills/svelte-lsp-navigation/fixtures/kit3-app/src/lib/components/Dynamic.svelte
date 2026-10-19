<script lang="ts">
  import CounterButton from "#lib/components/CounterButton.svelte";
  import { Counter } from "#lib/counter.svelte.js";
  import { formatCount } from "#lib/format.js";

  const counter = new Counter();
  let Active = $state(CounterButton);
  const lazy = import("#lib/components/CounterButton.svelte");
  const modules = import.meta.glob("./*.svelte");
  const handlers = { format: formatCount };
  let tag = $state("section");
</script>

<Active {counter} label="dynamic" />

{#await lazy then mod}
  <mod.default {counter} label="lazy" />
{/await}

<svelte:element this={tag}>{handlers.format(counter.count)}</svelte:element>

<p>{Object.keys(modules).length} modules</p>
