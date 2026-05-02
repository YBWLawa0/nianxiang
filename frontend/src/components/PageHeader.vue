<script setup lang="ts">
import { ref } from 'vue'
import { useFitText } from '../composables/useFitText'

const props = defineProps<{
  eyebrow?: string
  title: string
  subtitle?: string
}>()

const titleEl = ref<HTMLElement | null>(null)
useFitText(titleEl, { deps: () => [props.title] })
</script>

<template>
  <header class="page-header">
    <p v-if="eyebrow" class="eyebrow">{{ eyebrow }}</p>
    <h1 ref="titleEl" class="fit-text-title">{{ title }}</h1>
    <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
  </header>
</template>
