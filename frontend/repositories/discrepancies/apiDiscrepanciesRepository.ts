import ApiService from '@/services/api.service'
import { Distribution, MyProgress, Progress, MemberLabelChoices } from '~/domain/models/discrepancies/discrepancies'

export class APIDiscrepanciesRepository {
  constructor(private readonly request = ApiService) {}

  async fetchCategoryDistribution(projectId: string): Promise<Distribution> {
    const url = `/projects/${projectId}/metrics/category-distribution`
    const response = await this.request.get(url)
    return response.data
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

  async fetchMemberLabelChoices(projectId: string): Promise<MemberLabelChoices> {
    const url = `/projects/${projectId}/discrepancies/member-choices`
    const response = await this.request.get(url)
    return response.data
  }
}
