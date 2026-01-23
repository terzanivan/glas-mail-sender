<script setup lang="ts">
defineProps<{
  message: string
}>()
</script>

<template>
  <div v-if="message" class="mt-8 p-4 bg-red-50 text-glas-red rounded-2xl text-sm font-bold border border-red-100 flex items-center justify-center gap-2 animate-in shake duration-300">
     {{ message }}
  </div>
</template>
