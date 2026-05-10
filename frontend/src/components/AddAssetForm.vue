<template>
    <div class="card">

        <!-- Errore API globale -->
        <div v-if="apiError" class="alert alert--error">
            {{ apiError }}
        </div>

        <!-- Nome Asset -->
        <div class="form-group">
            <label class="form-label" for="name">
                Nome Asset <span class="required">*</span>
            </label>
            <input type="text" id="name" v-model.trim="form.name"
                :class="['form-control', errors.name ? 'is-invalid' : '']"
                placeholder="Es. Modulo Autenticazione Utente" maxlength="32" @input="clearError('name')">
            <p class="form-hint">La lunghezza del nome deve essere compresa tra 1 e 32 caratteri.</p>
            <p v-if="errors.name" class="form-error">{{ errors.name }}</p>
        </div>

        <!-- Tipo Asset -->
        <div class="form-group">
            <label class="form-label" for="asset_type">
                Tipo Asset <span class="required">*</span>
            </label>
            <select id="asset_type" v-model="form.asset_type"
                :class="['form-control', errors.asset_type ? 'is-invalid' : '']" @change="clearError('asset_type')">
                <option value="" disabled>Seleziona la tipologia dell'asset...</option>
                <option value="security">Security Asset</option>
                <option value="network">Network Asset</option>
            </select>
            <p v-if="errors.asset_type" class="form-error">{{ errors.asset_type }}</p>
        </div>

        <!-- Descrizione -->
        <div class="form-group">
            <label class="form-label" for="description">
                Descrizione <span class="required">*</span>
            </label>
            <textarea id="description" v-model.trim="form.description"
                :class="['form-control', errors.description ? 'is-invalid' : '']"
                placeholder="Fornisci una breve descrizione della funzione di questo asset..."
                @input="clearError('description')"></textarea>
            <p v-if="errors.description" class="form-error">{{ errors.description }}</p>
        </div>

        <!-- Bottoni azione -->
        <div class="action-bar">
            <a :href="cancelUrl" class="btn btn--secondary">Annulla</a>
            <button class="btn btn--success" :disabled="loading" @click="submitForm">
                <span v-if="loading" class="spinner"></span>
                {{ loading ? 'Salvataggio...' : 'Aggiungi Asset' }}
            </button>
        </div>

    </div>
</template>

<script>
export default {
    name: 'AddAssetForm',

    props: {
        sessionId: { type: String, required: true },
        deviceId: { type: String, required: true },
        cancelUrl: { type: String, required: true },
        redirectUrl: { type: String, required: true },
    },

    data() {
        return {
            form: {
                name: '',
                asset_type: '',
                description: '',
            },
            errors: {},
            apiError: null,
            loading: false,
        };
    },

    methods: {
        clearError(field) {
            delete this.errors[field];
            this.apiError = null;
        },

        validate() {
            const e = {};
            if (!this.form.name)
                e.name = 'Il nome è obbligatorio.';
            else if (this.form.name.length > 32)
                e.name = 'Il nome non può superare 32 caratteri.';
            if (!this.form.asset_type)
                e.asset_type = 'Seleziona una tipologia.';
            if (!this.form.description)
                e.description = 'La descrizione è obbligatoria.';
            this.errors = e;
            return Object.keys(e).length === 0;
        },

        async submitForm() {
            if (!this.validate()) return;

            this.loading = true;
            this.apiError = null;

            const url = `/api/sessions/${this.sessionId}/devices/${this.deviceId}/assets`;

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: this.form.name,
                        asset_type: this.form.asset_type,
                        description: this.form.description,
                    }),
                });

                if (response.status === 201) {
                    window.location.href = this.redirectUrl;
                } else {
                    const data = await response.json().catch(() => ({}));
                    this.apiError = data.error || `Errore ${response.status}: impossibile creare l'asset.`;
                }
            } catch {
                this.apiError = 'Errore di rete. Controlla la connessione e riprova.';
            } finally {
                this.loading = false;
            }
        },
    },
};
</script>