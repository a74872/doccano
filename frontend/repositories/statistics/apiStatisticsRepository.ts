// frontend/repositories/statistics/apiStatisticsRepository.ts
import ApiService from '@/services/api.service'

async function lastLabelDate(
  projectId:string, exId:number, user:string, uid?:number
): Promise<string|undefined> {
  // preferimos filter por id (mais rápido); se não houver, usamos username
  const params:any = { limit:1, ordering:'-created_at' }
  if (uid !== undefined) params.user = uid
  else                   params.username = user

  try {
    const res = await ApiService.get(
      `/projects/${projectId}/examples/${exId}/categories`,
      { params, headers:{Accept:'application/json'} }
    )
    const first = (Array.isArray(res.data) ? res.data : res.data.results)[0]
    return first?.created_at            // ISO string ou undefined
  } catch { return undefined }
}


interface Filters { member?: string }

/* ---------------- RELATÓRIO DE ANOTADOR ------------------------------- */
export class APIStatisticsRepository {
  async generateAnnotatorReport(projectId:string, { member }:Filters) {

    /* 0) — mapa username→id (ignora 500 silenciosamente) -------------- */
    let idByName:Record<string,number> = {}
    try {
      const mem = await ApiService.get(
        `/projects/${projectId}/members/`,
        { params:{ page_size:1000 }, headers:{Accept:'application/json'} }
      ).then(r => r.data.results ?? r.data)
      idByName = Object.fromEntries(mem.map((m:any)=>[m.username,m.id]))
    } catch {/* ok */ }

    /* 1) — exemplos ---------------------------------------------------- */
    const examples = await ApiService.get(
      `/projects/${projectId}/examples`,
      { params:{ page_size:1000 }, headers:{Accept:'application/json'} }
    ).then(r => r.data.results ?? r.data)

    const rows:any[] = []

    for (const ex of examples) {

      /* 1.1) distribuição de categorias para saber quem anotou -------- */
      const dist = await ApiService.get(
        `/projects/${projectId}/metrics/category-distribution`,
        { params:{ example:ex.id }, headers:{Accept:'application/json'} }
      ).then(r=>r.data)

      const users = member && member!=='ALL'
                  ? [member] : Object.keys(dist)

      for (const u of users) {
        const counts = dist[u] || {}
        const used   = Object.entries(counts).filter(([,n])=>+n>0)
        const total  = used.reduce((s,[,n])=>s+ +n,0)
        if (!total) continue                                  // sem rótulos

        /* 1.2) data da última label desse user ------------------------ */
        const rawDate = await lastLabelDate(
          projectId, ex.id, u, idByName[u]
        )

        /* 1.3) push da linha ----------------------------------------- */
        const exName = ex.upload_name
                    || ex.filename?.split('/').pop()
                    || `#${ex.id}`

        rows.push({
          annotator : u,
          example   : exName,
          date      : rawDate ? rawDate.replace('T',' ').slice(0,19) : '',
          total,
          categories: used.map(([lab])=>lab).sort().join(', ')
        })
      }
    }
    return { items: rows }
  }
}
