import ApiService from '@/services/api.service'
import { Distribution, MyProgress, Progress } from '~/domain/models/metrics/metrics'

export class APIMetricsRepository {
  constructor(private readonly request = ApiService) {}

  async fetchCategoryDistribution(projectId: string, params: { example?: number } = {}): Promise<Distribution> {
  const query = new URLSearchParams()
  if (params.example !== undefined) query.set('example', params.example.toString())

  const url = `/projects/${projectId}/metrics/category-distribution?${query}`
  const { data } = await this.request.get(url)
  return data
}

  async fetchSpanDistribution(projectId: string): Promise<Distribution> {
    const url = `/projects/${projectId}/metrics/span-distribution`
    const response = await this.request.get(url)
    return response.data
  }

  async fetchRelationDistribution(projectId: string): Promise<Distribution> {
    const url = `/projects/${projectId}/metrics/relation-distribution`
    const response = await this.request.get(url)
    return response.data
  }

  async fetchMemberProgress(projectId: string): Promise<Progress> {
    const url = `/projects/${projectId}/metrics/member-progress`
    const response = await this.request.get(url)
    return response.data
  }

  async fetchMyProgress(projectId: string): Promise<MyProgress> {
    const url = `/projects/${projectId}/metrics/progress`
    const response = await this.request.get(url)
    return response.data
  }
}
