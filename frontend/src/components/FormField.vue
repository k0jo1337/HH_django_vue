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
    <label v-if="field.labelTag === 'label'" :for="field.id || field.name">
      {{ field.label }}
    </label>
    <p v-else>{{ field.label }}</p>

    <select
      v-if="field.type === 'select'"
      :id="field.id || field.name"
      v-model="model"
      :required="field.required"
      :disabled="field.disabled"
    >
      <option
        v-if="field.placeholder"
        value=""
        disabled
      >
        {{ field.placeholder }}
      </option>
      <option
        v-for="option in field.options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>

    <textarea
      v-else-if="field.type === 'textarea'"
      :id="field.id || field.name"
      v-model="model"
      :required="field.required"
      :disabled="field.disabled"
      :readonly="field.readonly"
      :maxlength="field.maxlength"
      :rows="field.rows"
      :placeholder="field.placeholder"
    />

    <input
      v-else
      :id="field.id || field.name"
      v-model="model"
      :type="field.type || 'text'"
      :required="field.required"
      :disabled="field.disabled"
      :readonly="field.readonly"
      :autocomplete="field.autocomplete"
      :maxlength="field.maxlength"
      :placeholder="field.placeholder"
    >
  </div>
</template>
