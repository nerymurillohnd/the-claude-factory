<script lang="ts">
  import type { Snippet } from "svelte";
  import type { Counter } from "#lib/counter.svelte.js";
  import { formatCount } from "#lib/format.js";

  interface Props {
    counter: Counter;
    label: string;
    children?: Snippet;
  }

  let { counter, label, children }: Props = $props();
</script>

<button type="button" onclick={() => counter.increment()}>
  {label}: {formatCount(counter.count)}
</button>
{@render children?.()}
