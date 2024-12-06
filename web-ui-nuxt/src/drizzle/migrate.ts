import { drizzle } from 'drizzle-orm/postgres-js';
import { migrate } from 'drizzle-orm/postgres-js/migrator';
import postgres from 'postgres';
import * as schema from './schema';

const runMigration = async () => {
  const connection = postgres(process.env.DATABASE_URL!);
  const db = drizzle(connection, { schema });

  console.log('Running migrations...');
  await migrate(db, { migrationsFolder: 'drizzle/migrations' });
  console.log('Migrations completed!');

  await connection.end();
};

runMigration().catch(console.error);
