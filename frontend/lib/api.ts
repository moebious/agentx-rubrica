/**
 * Rubrica API Client
 *
 * This file will be auto-generated from FastAPI OpenAPI spec.
 * For now, it's a skeleton implementation.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface IncidentIntake {
  description: string;
  screenshot_base64?: string;
  logs_text?: string;
  reporter_email?: string;
  severity?: string;
}

export interface IncidentSubmissionResponse {
  incident_id: string;
  status: string;
  message: string;
}

/**
 * Submit a new incident
 */
export async function submitIncident(
  data: IncidentIntake
): Promise<IncidentSubmissionResponse> {
  // TODO: Implement actual API call
  console.log('Submitting incident:', data);
  throw new Error('Not implemented yet');
}

/**
 * Get incident status
 */
export async function getIncident(incidentId: string) {
  // TODO: Implement actual API call
  console.log('Getting incident:', incidentId);
  throw new Error('Not implemented yet');
}

/**
 * Health check
 */
export async function healthCheck() {
  const response = await fetch(`${API_URL}/api/v1/health`);
  return response.json();
}
