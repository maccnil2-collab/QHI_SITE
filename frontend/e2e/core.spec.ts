import { randomUUID } from "node:crypto";
import { expect, test } from "@playwright/test";
import type { APIRequestContext } from "@playwright/test";

const apiUrl = process.env.QHI_E2E_API_URL!;

async function integrationVehicle(request: APIRequestContext) {
  const response = await request.get(`${apiUrl}/cars`, { params: { locale: "en", q: "Integration" } });
  expect(response.ok(), await response.text()).toBeTruthy();
  const cars = await response.json() as { id: number; slug: string; localized_title: string | null; brand: string }[];
  const car = cars.find((item) => item.brand === "Integration");
  expect(car, "Run backend/tests/test_postgres_workflows.py first to seed a published test vehicle and active tariff.").toBeTruthy();
  return car!;
}

test("RU, Tajik and English routes render and vehicle details are reachable", async ({ page, request }) => {
  const car = await integrationVehicle(request);
  for (const locale of ["ru", "tg", "en"]) {
    const response = await page.goto(`/${locale}`);
    expect(response?.ok()).toBeTruthy();
    await expect(page.locator("main")).toBeVisible();
  }

  await page.goto("/en");
  await page.getByRole("textbox", { name: "Make, model or trim" }).fill("Integration");
  const vehicleLink = page.getByRole("link", { name: car.localized_title ?? "Integration EV" }).first();
  await expect(vehicleLink).toBeVisible();
  await vehicleLink.click();
  await expect(page.locator(".vehicle-summary h1")).toHaveText(car.localized_title ?? "Integration EV");
});

test("customer registers, restores their session, saves a quote and creates an order", async ({ page, request }) => {
  const car = await integrationVehicle(request);
  const email = `e2e-${randomUUID()}@example.test`;
  const password = "QHI-E2E-Strong-Password-2026!";

  await page.goto("/en/account");
  await page.getByRole("button", { name: "Create account" }).first().click();
  await page.getByLabel("Full name").fill("QHI E2E Customer");
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Create account" }).last().click();
  await expect(page.getByRole("heading", { name: "QHI E2E Customer" })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("heading", { name: "QHI E2E Customer" })).toBeVisible();

  await page.goto("/en");
  await page.getByLabel("Make, model or trim").fill("Integration");
  await page.getByRole("link", { name: car.localized_title ?? "Integration EV" }).first().click();
  const priceInput = page.getByLabel("Vehicle price in China, CNY");
  await priceInput.fill("10000");
  await expect(priceInput).toHaveValue("10000");
  await page.getByRole("button", { name: "Calculate estimate" }).click();
  await expect(page.locator(".quote-total")).toBeVisible();

  await page.goto("/en/account");
  const savedEstimates = page.locator(".account-block").filter({ has: page.getByRole("heading", { name: "Cost estimates" }) });
  await expect(savedEstimates.locator(".account-record")).toHaveCount(1);
  await page.getByLabel("Vehicle ID").fill(String(car.id));
  await page.getByLabel("Message").fill("Playwright order request");
  await page.getByRole("button", { name: "Submit request" }).click();
  await expect(page.getByText("Request created")).toBeVisible();
  await expect(page.locator(".account-record").filter({ hasText: "Integration EV" })).toBeVisible();
});

test("staff manages a CRM lead and the admin catalog panel connects", async ({ page, request }) => {
  const marker = randomUUID();
  const staffEmail = `e2e-staff-${marker}@example.test`;
  const password = "QHI-E2E-Strong-Password-2026!";
  const leadName = `E2E Lead ${marker}`;

  const lead = await request.post(`${apiUrl}/leads`, { data: {
    name: leadName, email: `lead-${marker}@example.test`, preferred_locale: "en", message: "Playwright CRM enquiry",
  } });
  expect(lead.status(), await lead.text()).toBe(201);

  const registration = await request.post(`${apiUrl}/auth/register`, { data: {
    email: staffEmail, password, full_name: "QHI E2E Manager", preferred_locale: "en",
  } });
  expect(registration.status(), await registration.text()).toBe(201);
  const staff = (await registration.json()).customer as { id: number };
  const promoted = await request.patch(`${apiUrl}/admin/customers/${staff.id}/role`, {
    headers: { "X-Admin-Token": process.env.QHI_E2E_ADMIN_API_KEY! }, data: { role: "manager" },
  });
  expect(promoted.ok(), await promoted.text()).toBeTruthy();

  await page.goto("/admin/crm");
  await page.locator(".crm-language select").selectOption("en");
  await page.getByLabel("Email").fill(staffEmail);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in" }).click();
  const leadCard = page.locator(".crm-lead").filter({ has: page.getByRole("heading", { name: leadName }) });
  await expect(leadCard).toBeVisible();
  await leadCard.locator(".crm-controls select").first().selectOption("contacted");
  await expect(leadCard).toContainText("Contacted");

  await page.goto("/admin");
  await page.locator(".admin-connect input").fill(process.env.QHI_E2E_ADMIN_API_KEY!);
  await page.locator(".admin-connect button").click();
  await expect(page.locator(".admin-tabs")).toBeVisible();
});
