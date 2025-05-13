// frontend/domain/models/perspective/perspective.ts
export type DataType = "string" | "int" | "choice";

export interface ChoiceOption { value: string }

export interface Label {
  id?: number;
  name: string;
  data_type: DataType;
  int_min?: number;
  int_max?: number;
  options?: ChoiceOption[];
}

export interface Perspective {
  id: number;
  title: string;
  project: number;
  labels: Label[];
  created_by?: string;
  created_at?: string;
}

/** payload usado no POST (id, project e created_* são preenchidos no backend) */
export type CreatePerspectiveDTO = Pick<Perspective, "title" | "labels">;
