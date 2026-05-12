<script setup>
const model = defineModel();

defineProps({
  field: {
    type: Object,
    required: true,
  },
  wrapperClass: {
    type: String,
    default: "input_form",
  },
});
</script>

<template>
  <label v-if="field.type === 'checkbox'" :class="['form-checkbox', field.class]">
    <input
      v-model="model"
      type="checkbox"
      :disabled="field.disabled"
    >
    <span>{{ field.label }}</span>
  </label>

  <div v-else :class="field.class || wrapperClass">
    <p>{{ field.label }}</p>
    <input
      v-model="model"
      :type="field.type || 'text'"
      :required="field.required"
      :disabled="field.disabled"
      :readonly="field.readonly"
      :autocomplete="field.autocomplete"
    >
  </div>
</template>
