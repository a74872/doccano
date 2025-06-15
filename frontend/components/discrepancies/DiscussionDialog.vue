<template>
  <v-dialog :value="value" @input="$emit('input', $event)"
      max-width="640"
      max-height="80vh"
      scrollable>
    <v-card height="550" class="d-flex flex-column">

      <!-- cabeçalho -->
      <v-card-title class="headline">
        Discussion
        <v-spacer/>
        <v-btn icon @click="$emit('input', false)">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <!-- mensagens -->
      <v-card-text ref="scrollArea" class="scroll-area">
        <template v-if="loading">
          <v-skeleton-loader type="paragraph"/>
        </template>

        <v-slide-y-transition group appear v-else>
          <div
            v-for="msg in messages"
            :key="msg.id"
            :class="['msg-wrapper', msg.username === me ? 'mine' : 'theirs']"
          >
            <div class="bubble">
              {{ msg.text }}
            </div>
            <small class="meta">
              {{ msg.username }} · {{ human(msg.created_at) }}
            </small>
          </div>
        </v-slide-y-transition>
      </v-card-text>

      <!-- input -->
      <v-divider/>
      <v-card-actions>
        <v-text-field
          v-model="draft"
          dense outlined hide-details
          placeholder="Write a message …"
          class="flex-grow-1"
          @keyup.enter="send"
          :disabled="sending"
        />
        <v-btn 
          color="primary" 
          text 
          :disabled="!draft.trim() || sending" 
          :loading="sending"
          @click="send"
        >
          Send
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Snackbar para erros -->
    <v-snackbar
      v-model="showError"
      color="error"
      timeout="5000"
      top
    >
      {{ errorMessage }}
      <template v-slot:action="{ attrs }">
        <v-btn
          text
          v-bind="attrs"
          @click="showError = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
dayjs.extend(relativeTime)

export default Vue.extend({
  props: {
    value:     { type: Boolean, required: true },
    projectId: { type: String,  required: true },
    example:   { type: Object,  required: true }
  },
  data () {
    return { 
      messages: [], 
      loading: false, 
      sending: false,
      draft: '',
      showError: false,
      errorMessage: ''
    }
  },
  computed: {
    me () { return this.$auth?.user?.username || '' }
  },
  mounted () { this.scrollBottom() },
  watch: {
    value (v) { v && this.fetch() },
    example  () { this.value && this.fetch() },
    messages () { this.$nextTick(this.scrollBottom) }
  },
  methods: {
    human (ts:string){ return dayjs(ts).fromNow() },
    scrollBottom () {
      const el = this.$refs.scrollArea as HTMLElement
      if (el) el.scrollTop = el.scrollHeight
    },

    showErrorMessage(message: string) {
      this.errorMessage = message
      this.showError = true
    },

    getErrorMessage(error: any): string {
      // Verifica diferentes tipos de erro
      if (error.response) {
        const status = error.response.status
        const data = error.response.data
        
        // Erros específicos da base de dados
        if (status >= 500) {
          return 'Erro de Base de Dados. Tente novamente mais tarde'
        }
        
        // Outros erros HTTP
        if (status === 404) {
          return 'Recurso não encontrado'
        }
        
        if (status === 403) {
          return 'Não tem permissão para esta ação'
        }
        
        if (status === 401) {
          return 'Sessão expirada. Faça login novamente'
        }
        
        // Mensagem personalizada do servidor
        if (data && data.message) {
          return data.message
        }
        
        return `Erro HTTP ${status}`
      }
      
      // Erro de rede/conectividade
      if (error.code === 'NETWORK_ERROR' || !error.response) {
        return 'Erro de conectividade. Verifique sua internet'
      }
      
      // Timeout
      if (error.code === 'ECONNABORTED') {
        return 'Timeout na operação. Tente novamente'
      }
      
      // Erro genérico
      return 'Ocorreu um erro inesperado'
    },

    async fetch () {
      this.loading = true
      try {
        const url = `/v1/projects/${this.projectId}/examples/${this.example.id}/discussion/messages/`
        const data = await this.$axios.$get(url)
        this.messages = (Array.isArray(data) ? data : data.results).slice().reverse()
      } catch (error) {
        console.error('Erro ao carregar mensagens:', error)
        this.showErrorMessage(this.getErrorMessage(error))
      } finally { 
        this.loading = false 
      }
    },

    async send () {
      const text = this.draft.trim()
      if (!text) return
      
      this.sending = true
      const originalDraft = this.draft
      
      try {
        const url = `/v1/projects/${this.projectId}/examples/${this.example.id}/discussion/messages/`
        await this.$axios.$post(url, { example: this.example.id, text })
        
        // Adiciona mensagem temporária
        this.messages.unshift({
          id : Date.now(),
          username : this.me,
          created_at: new Date().toISOString(),
          text
        })
        
        this.$nextTick(this.scrollBottom)
        this.draft = ''
        
        // Recarrega mensagens para sincronizar
        await this.fetch()
        
      } catch (error) {
        console.error('Erro ao enviar mensagem:', error)
        
        // Restaura o draft em caso de erro
        this.draft = originalDraft
        
        this.showErrorMessage(this.getErrorMessage(error))
      } finally {
        this.sending = false
      }
    }
  }
})
</script>

<style>
.scroll-area{
  flex:1 1 auto;
  overflow-y:auto;
}

:deep(.msg-wrapper){
  max-width:75%;
  display:flex;
  flex-direction:column;
  margin:6px 0;
}

.meta{
  font-size:.85rem;
  padding:0rem 12rem;
  color:#4682B4;
}

/* bolha */
.bubble{
  padding:.40rem .0rem;
  border-radius:18px;
  box-shadow:0 1px 7px rgba(0,0,0,.99);
  white-space:pre-wrap;
  word-break:break-word;
  line-height:1rem;
  background:#87CEEB;
  color:Black;
  margin-top: 9px;
  margin-bottom: 5px;
}
</style>