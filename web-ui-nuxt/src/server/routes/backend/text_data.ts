import { createError } from 'h3'
import type { Database } from '~~/types/database.types'
import { serverSupabaseClient } from '#supabase/server'

export default defineEventHandler(async (event) => {
  const client = await serverSupabaseClient<Database>(event);

  const { data, error } = await client.from('Text_data').select('text_id, en_sentence, sentence_length_group')
  if (error) {
    throw createError({ statusMessage: error.message })
  }

  return data
})
