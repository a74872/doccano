import axios from "axios";

export const apiPerspectiveRepository = {
  async getPerspectives(projectId: number): Promise<Perspective[]> {
    const { data } = await axios.get(`/v1/projects/${projectId}/perspective`);
    return data;
  },

  async createPerspective(projectId: number, payload: Partial<Perspective>) {
    await axios.post(`/v1/projects/${projectId}/perspective`, payload);
  }
};
