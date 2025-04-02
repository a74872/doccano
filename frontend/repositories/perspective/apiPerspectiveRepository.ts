import axios from "axios"; // Import externo deve vir primeiro
import { Perspective } from "@/domain/models/perspective/perspective"; // Import interno vem depois

export const apiPerspectiveRepository = {
  async getPerspectives(projectId: number): Promise<Perspective[]> {
        const { data } = await axios.get(`/v1/projects/${projectId}/perspective`);
    return data;
  },

  async createPerspective(projectId: number, payload: Partial<Perspective>) {
    await axios.post(`/v1/projects/${projectId}/perspective`, payload);
  }
};