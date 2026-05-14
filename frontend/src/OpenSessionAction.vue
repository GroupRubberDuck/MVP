<template>
  <!-- Componente coordinatore -->
</template>

<script setup>
import { onMounted } from 'vue';

const openSession = async (deviceId) => {
  try {
    const response = await fetch('/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ device_id: deviceId }),
    });

    const contentType = response.headers.get("content-type");

    if (!response.ok) {
      let message = 'C\'è già una sessione attiva per questo o un altro dispositivo.';
      if (contentType && contentType.includes("application/json")) {
        const errorData = await response.json();
        message = errorData.error || message;
      }
      throw new Error(message);
    }

    const data = await response.json();

    // Redirect diretto alla dashboard
    window.location.href = `/dashboard/sessions/${data.session_id}/devices/${deviceId}`;

  } catch (error) {
    alert(error.message);
  }
};

onMounted(() => {
  window.openSessionAction = openSession;
});
</script>