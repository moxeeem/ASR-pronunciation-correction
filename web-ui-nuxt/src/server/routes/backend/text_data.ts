import { createError } from 'h3'
import type { Database } from '~~/types/database.types'

export default defineEventHandler(async (event) => {
  const client = await serverSupabaseClient<Database>(event)

  const { data, error } = await client.from('Text_data').select('text_id')
  if (error) {
    throw createError({ statusMessage: error.message })
  }

  return data
})
