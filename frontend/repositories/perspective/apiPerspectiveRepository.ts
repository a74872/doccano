export const apiPerspectiveRepository = {
  async getPerspectives(projectId: number): Promise<Perspective[]> {
    await Promise.resolve(); // Dummy await
    return Promise.resolve([
      {
        id: 1,
        name: "Exemplo de Perspectiva",
        data_type: "string",
        project: projectId,
        created_by: "usuário_exemplo",
        created_at: "2023-01-01T00:00:00Z",
      },
      {
        id: 2,
        name: "Outra Perspectiva",
        data_type: "integer",
        project: projectId,
        created_by: "usuário_exemplo",
        created_at: "2023-01-02T00:00:00Z",
      },
    ]);
  },

  async createPerspective(projectId: number, payload: Partial<Perspective>): Promise<void> {
    await Promise.resolve(); // Dummy await
    console.log("Mock createPerspective chamado com:", projectId, payload);
    return Promise.resolve();
  }
};
