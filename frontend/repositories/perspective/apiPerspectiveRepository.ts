import axios from "axios";
import { Perspective } from "@/domain/models/perspective/perspective"; // Adjust the import as needed

export const apiPerspectiveRepository = {
  async getPerspectives(projectId: number): Promise<Perspective[]> {
    const { data } = await axios.get(`/v1/projects/${projectId}/perspective`);
    return data;
  },

    // New method to support search and pagination
  async listPerspectives(projectId: number, query: any): Promise<{ results: Perspective[]; count: number }> {
    const queryString = new URLSearchParams(query).toString();
    const { data } = await axios.get(`/v1/projects/${projectId}/perspective?${queryString}`);
    return data;
  },

  async createPerspective(projectId: number, payload: CreatePerspectiveDTO) {
    const { data } = await axios.post(`/v1/projects/${projectId}/perspective`, payload);
    return data;
  },


  async deletePerspective(projectId: number, perspectiveId: number): Promise<void> {
    await axios.delete(`/v1/projects/${projectId}/perspective/${perspectiveId}`);
  },

  async getPerspectiveDetails(projectId: number, perspectiveId: number): Promise<Perspective> {
    const { data } = await axios.get(`/v1/projects/${projectId}/perspective/${perspectiveId}`);
    return data;
  },
};
