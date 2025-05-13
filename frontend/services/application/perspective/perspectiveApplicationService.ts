import { apiPerspectiveRepository } from "@/repositories/perspective/apiPerspectiveRepository";
import { CreatePerspectiveDTO, Perspective } from "@/domain/models/perspective/perspective";

export class PerspectiveApplicationService {
  private repository: typeof apiPerspectiveRepository;

  constructor(repository: typeof apiPerspectiveRepository) {
    this.repository = repository;
  }

  async fetchPerspectives(projectId: number): Promise<Perspective[]> {
    return await this.repository.getPerspectives(projectId);
  }

  async createPerspective(projectId: number, payload: CreatePerspectiveDTO): Promise<Perspective> {
    return await this.repository.createPerspective(projectId, payload);
  }

  async deletePerspective(projectId: number, perspectiveId: number) {
    await this.repository.deletePerspective(projectId, perspectiveId);
  }

  async getPerspectiveDetails(projectId: number, perspectiveId: number): Promise<Perspective> {
    return await this.repository.getPerspectiveDetails(projectId, perspectiveId);
  }
}