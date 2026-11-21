import { apiGet, type QueryParams } from './client'
import type {
  Filters,
  JobDistanceResponse,
  JobOptionsResponse,
  JobProfileResponse,
  MetaResponse,
  OverviewResponse,
  RecordsResponse,
  RegionsResponse,
  SimilarRegionsResponse,
} from './types'

/**
 * 页面唯一的数据入口（组件内禁止直接 fetch / 直接拼路径）。
 * 路径按 协作契约 V1 的 /api/v1 前缀；本文件中的参数名是待确认假设，
 * 见 docs/design/request_contract_notes.md。
 */

function filterParams(filters: Filters): QueryParams {
  return {
    region: filters.regions,
    industry: filters.industries,
    job: filters.jobs,
    education: filters.educations,
    experience: filters.experiences,
  }
}

export const api = {
  meta(signal?: AbortSignal): Promise<MetaResponse> {
    return apiGet<MetaResponse>('/meta', undefined, signal)
  },

  jobOptions(q: string, page: number, pageSize: number, signal?: AbortSignal): Promise<JobOptionsResponse> {
    return apiGet<JobOptionsResponse>('/options/jobs', { q, page, pageSize }, signal)
  },

  overview(filters: Filters, signal?: AbortSignal): Promise<OverviewResponse> {
    return apiGet<OverviewResponse>('/overview', filterParams(filters), signal)
  },

  regions(filters: Filters, signal?: AbortSignal): Promise<RegionsResponse> {
    return apiGet<RegionsResponse>('/regions', filterParams(filters), signal)
  },

  jobProfile(filters: Filters, job: string, signal?: AbortSignal): Promise<JobProfileResponse> {
    return apiGet<JobProfileResponse>('/jobs/profile', { ...filterParams(filters), job }, signal)
  },

  jobDistance(filters: Filters, jobs: string[], signal?: AbortSignal): Promise<JobDistanceResponse> {
    return apiGet<JobDistanceResponse>('/jobs/distance', { ...filterParams(filters), job: jobs }, signal)
  },

  similarRegions(region: string, signal?: AbortSignal): Promise<SimilarRegionsResponse> {
    return apiGet<SimilarRegionsResponse>('/regions/similar', { region }, signal)
  },

  records(filters: Filters, page: number, pageSize: number, signal?: AbortSignal): Promise<RecordsResponse> {
    return apiGet<RecordsResponse>('/records', { ...filterParams(filters), page, pageSize }, signal)
  },
}
