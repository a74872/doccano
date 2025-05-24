// frontend/repositories/statistics/apiStatisticsRepository.ts
import ApiService from '@/services/api.service'

interface Filters { member: string }

export class APIStatisticsRepository {
  private readonly req = ApiService

  /* helper: varre toda a paginação DRF */
  private async fetchAll (path: string, params: any = {}): Promise<any[]> {
    let url   = path
    let first = true
    const out:any[] = []

    while (url) {
      const res  = await this.req.get(url, first ? { params } : undefined)
      const data = res.data
      out.push(...(Array.isArray(data) ? data : data.results))
      url   = Array.isArray(data) ? null
            : data.next ? data.next.replace(/^https?:\/\/[^/]+\/v1/, '') : null
      first = false
    }
    return out
  }

  /* ───── Relatório de Anotador ───── */
  async generateAnnotatorReport (projectId: string, { member }: Filters) {
    console.log('[generateAnnotatorReport] member =', member)
    if (!member) return { items: [] }

    /* 1) – lista de exemplos (já sem “/” no fim) */
    const examples = await this.fetchAll(
      `/projects/${projectId}/examples`,      // ← sem barra final
      { limit: 200, offset: 0, q: '' }
    )
    console.log('[fetchAll] total items:', examples.length, examples.map(e => e.id))

    /* 2) – percorre exemplos */
    const datasets:any[] = []
    let grandTotal = 0
    const globalCounts: Record<string, number> = {}

    for (const ex of examples) {
      console.log('[dist] GET /projects/'+projectId+'/metrics/category-distribution  example=', ex.id)

      /* chama métricas; se falhar (500) salta o example */
      let dist:any
      try {
        dist = await this.req.get(
          `/projects/${projectId}/metrics/category-distribution`,
          { params: { example: ex.id } }
        ).then(r => r.data)
      } catch (err) {
        console.warn('[dist] 500 – ignorado example', ex.id)
        continue
      }

      const userCounts = dist[member] || {}
      const exTotal    = Object.values(userCounts)
                               .reduce((a,c)=>a+Number(c), 0)
      if (!exTotal) continue

      grandTotal += exTotal
      for (const [lab, n] of Object.entries(userCounts))
        globalCounts[lab] = (globalCounts[lab]||0) + Number(n)

      datasets.push({
        document: ex.id,
        categories: Object.entries(userCounts).map(([lab, n]) => ({
          name : lab,
          count: Number(n),
          percentage: ((Number(n)/exTotal)*100).toFixed(1)
        }))
      })
    }

    return {
      items: [{
        annotator : member,
        total     : grandTotal,
        categories: Object.keys(globalCounts).sort().join(', '),
        disagreementRate: undefined,
        datasets
      }]
    }
  }
}
