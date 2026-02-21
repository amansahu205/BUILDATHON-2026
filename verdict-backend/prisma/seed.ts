/**
 * VERDICT — dev seed
 * Creates: 1 firm, 3 users, 2 cases, 1 witness
 * Run: npx prisma db seed
 */
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import { db } from '../src/lib/db.js';

const PASSWORD_HASH = await bcrypt.hash('Demo!Pass123', 12);

async function main() {
  // ── 1. Firm ──────────────────────────────────────────────────────────────
  const firm = await db.firm.upsert({
    where: { slug: 'demo-law-group' },
    create: {
      name: 'Demo Law Group LLP',
      slug: 'demo-law-group',
      seats: 10,
      plan: 'professional',
      setupComplete: true,
      retentionDays: 90,
    },
    update: { plan: 'professional' },
  });
  console.log('✓ Firm:', firm.id, firm.name);

  // ── 2. Users ─────────────────────────────────────────────────────────────
  const sarah = await db.user.upsert({
    where: { email: 'sarah.chen@demo.com' },
    create: {
      firmId: firm.id,
      email: 'sarah.chen@demo.com',
      name: 'Sarah Chen',
      role: 'PARTNER',
      passwordHash: PASSWORD_HASH,
      emailVerified: true,
    },
    update: {},
  });
  console.log('✓ User (PARTNER):', sarah.id, sarah.email);

  const james = await db.user.upsert({
    where: { email: 'j.rodriguez@demo.com' },
    create: {
      firmId: firm.id,
      email: 'j.rodriguez@demo.com',
      name: 'James Rodriguez',
      role: 'ASSOCIATE',
      passwordHash: PASSWORD_HASH,
      emailVerified: true,
    },
    update: {},
  });
  console.log('✓ User (ASSOCIATE):', james.id, james.email);

  const admin = await db.user.upsert({
    where: { email: 'admin@demo.com' },
    create: {
      firmId: firm.id,
      email: 'admin@demo.com',
      name: 'Admin User',
      role: 'ADMIN',
      passwordHash: PASSWORD_HASH,
      emailVerified: true,
    },
    update: {},
  });
  console.log('✓ User (ADMIN):', admin.id, admin.email);

  // ── 3. Cases ─────────────────────────────────────────────────────────────
  const case1 = await db.case.upsert({
    where: { id: 'seed-case-chen-v-metro' },
    create: {
      id: 'seed-case-chen-v-metro',
      firmId: firm.id,
      ownerId: sarah.id,
      name: 'Chen v. Metropolitan Hospital',
      caseType: 'MEDICAL_MALPRACTICE',
      opposingFirm: 'Defense Partners LLP',
      depositionDate: new Date('2026-03-15'),
    },
    update: {},
  });
  console.log('✓ Case 1:', case1.id, case1.name);

  const case2 = await db.case.upsert({
    where: { id: 'seed-case-thompson-v-axiom' },
    create: {
      id: 'seed-case-thompson-v-axiom',
      firmId: firm.id,
      ownerId: sarah.id,
      name: 'Thompson v. Axiom Industries',
      caseType: 'EMPLOYMENT_DISCRIMINATION',
      opposingFirm: 'Axiom Legal Team',
      depositionDate: new Date('2026-02-26'),
    },
    update: {},
  });
  console.log('✓ Case 2:', case2.id, case2.name);

  // ── 4. Witness ───────────────────────────────────────────────────────────
  const witness = await db.witness.upsert({
    where: { id: 'seed-witness-emily-chen' },
    create: {
      id: 'seed-witness-emily-chen',
      caseId: case1.id,
      firmId: firm.id,
      name: 'Dr. Emily Chen',
      email: 'emily.chen@metro.com',
      role: 'DEFENDANT',
      notes: 'Known weakness: medication dosage timeline discrepancy',
    },
    update: {},
  });
  console.log('✓ Witness:', witness.id, witness.name);

  // ── Summary ──────────────────────────────────────────────────────────────
  console.log('\n── Seed complete ──────────────────────────────────');
  console.log({ firmId: firm.id, users: [sarah.id, james.id, admin.id], cases: [case1.id, case2.id], witnessId: witness.id });
  console.log('\nLogin with: sarah.chen@demo.com / Demo!Pass123');
}

main()
  .catch((e) => { console.error(e); process.exit(1); })
  .finally(() => db.$disconnect());
