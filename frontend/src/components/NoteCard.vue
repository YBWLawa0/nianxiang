<script setup lang="ts">
import type { Note } from '../types/domain'
import { formatDateTime } from '../utils/date'

defineProps<{ note: Note; compact?: boolean }>()
</script>

<template>
  <article class="note-card" :class="{ compact }">
    <div class="note-meta">
      <span>{{ formatDateTime(note.created_at) }}</span>
      <span class="energy-pill">能量 {{ note.energy_score }}</span>
    </div>
    <p class="note-content">{{ note.content }}</p>
    <div class="note-tags">
      <span>{{ note.grid_tag }}</span>
      <span v-if="!compact">{{ note.ai_comment }}</span>
    </div>
  </article>
</template>
