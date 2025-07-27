import { Page, Locator, expect } from '@playwright/test';
import { TestData, Timeouts } from '../utils/test-data';
import { TestHelpers } from '../utils/helpers';

/**
 * Page Object Model for the Setup tab
 */
export class SetupTab {
  readonly page: Page;
  
  // Input fields
  readonly brandInput: Locator;
  readonly competitorInput: Locator;
  
  // Industry selection
  readonly industrySelector: Locator;
  readonly bankingCard: Locator;
  readonly techCard: Locator;
  readonly healthcareCard: Locator;
  
  // Analysis area dropdown
  readonly analysisAreaDropdown: Locator;
  
  // Action buttons
  readonly startAnalysisButton: Locator;
  readonly viewChartsButton: Locator;
  readonly deepDiveButton: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Look for input fields by placeholder text or labels
    this.brandInput = page.locator('input').filter({ hasText: /brand|company/i }).first()
      .or(page.locator('input[placeholder*="brand"]')).first()
      .or(page.locator('input[placeholder*="company"]')).first()
      .or(page.locator('textarea').first()); // Flutter might use textarea
    
    this.competitorInput = page.locator('input').filter({ hasText: /competitor/i }).first()
      .or(page.locator('input[placeholder*="competitor"]')).first();
    
    // Industry cards - look for clickable elements with industry info
    this.industrySelector = page.locator('.industry-selector, [role="radiogroup"]').first();
    
    this.bankingCard = page.locator('*').filter({ hasText: TestData.INDUSTRY_DEMOS.BANKING.title }).first()
      .or(page.locator('*').filter({ hasText: /banking|bank/i })).first();
    
    this.techCard = page.locator('*').filter({ hasText: TestData.INDUSTRY_DEMOS.TECH.title }).first()
      .or(page.locator('*').filter({ hasText: /technology|tech/i })).first();
    
    this.healthcareCard = page.locator('*').filter({ hasText: TestData.INDUSTRY_DEMOS.HEALTHCARE.title }).first()
      .or(page.locator('*').filter({ hasText: /healthcare|health/i })).first();
    
    // Dropdown for analysis area
    this.analysisAreaDropdown = page.locator('select, [role="combobox"], [role="listbox"]').first()
      .or(page.locator('*').filter({ hasText: /analysis area|select area/i })).first();
    
    // Action buttons
    this.startAnalysisButton = page.locator('button').filter({ hasText: /start|analyze|begin/i }).first();
    this.viewChartsButton = page.locator('button').filter({ hasText: /view charts|charts/i }).first();
    this.deepDiveButton = page.locator('button').filter({ hasText: /deep dive|details/i }).first();
  }

  /**
   * Fill in brand name
   */
  async enterBrandName(brandName: string): Promise<void> {
    await this.brandInput.waitFor({ state: 'visible', timeout: Timeouts.MEDIUM });
    await this.brandInput.fill(brandName);
    await this.page.waitForTimeout(500); // Wait for input processing
  }

  /**
   * Select industry
   */
  async selectIndustry(industry: keyof typeof TestData.INDUSTRIES): Promise<void> {
    let industryCard: Locator;
    
    switch (industry) {
      case 'BANKING':
        industryCard = this.bankingCard;
        break;
      case 'TECH':
        industryCard = this.techCard;
        break;
      case 'HEALTHCARE':
        industryCard = this.healthcareCard;
        break;
      default:
        throw new Error(`Unknown industry: ${industry}`);
    }

    await industryCard.waitFor({ state: 'visible', timeout: Timeouts.MEDIUM });
    await industryCard.click();
    await TestHelpers.waitForAnimation(this.page);
  }

  /**
   * Select analysis area from dropdown
   */
  async selectAnalysisArea(area: string): Promise<void> {
    if (await this.analysisAreaDropdown.isVisible({ timeout: Timeouts.SHORT })) {
      await this.analysisAreaDropdown.click();
      
      // Look for option in dropdown
      const option = this.page.locator('option, [role="option"]').filter({ hasText: area }).first()
        .or(this.page.locator('*').filter({ hasText: area })).first();
      
      await option.click();
      await TestHelpers.waitForAnimation(this.page);
    }
  }

  /**
   * Enter competitor name
   */
  async enterCompetitorName(competitorName: string): Promise<void> {
    if (await this.competitorInput.isVisible({ timeout: Timeouts.SHORT })) {
      await this.competitorInput.fill(competitorName);
      await this.page.waitForTimeout(500);
    }
  }

  /**
   * Start analysis process
   */
  async startAnalysis(): Promise<void> {
    await this.startAnalysisButton.waitFor({ state: 'visible', timeout: Timeouts.MEDIUM });
    await this.startAnalysisButton.click();
    
    // Wait for analysis to begin
    await this.page.waitForTimeout(2000);
  }

  /**
   * Click View Charts button
   */
  async viewCharts(): Promise<void> {
    await this.viewChartsButton.waitFor({ state: 'visible', timeout: Timeouts.MEDIUM });
    await this.viewChartsButton.click();
    await TestHelpers.waitForAnimation(this.page);
  }

  /**
   * Click Deep Dive button
   */
  async deepDive(): Promise<void> {
    if (await this.deepDiveButton.isVisible({ timeout: Timeouts.SHORT })) {
      await this.deepDiveButton.click();
      await TestHelpers.waitForAnimation(this.page);
    }
  }

  /**
   * Complete full setup workflow
   */
  async completeSetup(
    brandName: string, 
    industry: keyof typeof TestData.INDUSTRIES,
    analysisArea: string,
    competitorName?: string
  ): Promise<void> {
    await this.enterBrandName(brandName);
    await this.selectIndustry(industry);
    await this.selectAnalysisArea(analysisArea);
    
    if (competitorName) {
      await this.enterCompetitorName(competitorName);
    }
    
    await this.startAnalysis();
  }

  /**
   * Verify setup form is visible and functional
   */
  async verifySetupForm(): Promise<void> {
    // Check that main input elements are present
    await expect(this.brandInput).toBeVisible();
    
    // Verify industry selection options are available
    const industries = [this.bankingCard, this.techCard, this.healthcareCard];
    const visibleIndustries = await Promise.all(
      industries.map(card => card.isVisible({ timeout: Timeouts.SHORT }))
    );
    
    expect(visibleIndustries.some(visible => visible)).toBe(true);
  }

  /**
   * Get selected industry
   */
  async getSelectedIndustry(): Promise<string | null> {
    const industries = [
      { card: this.bankingCard, name: 'Banking' },
      { card: this.techCard, name: 'Technology' },
      { card: this.healthcareCard, name: 'Healthcare' }
    ];

    for (const industry of industries) {
      const className = await industry.card.getAttribute('class') || '';
      if (className.includes('selected') || className.includes('active')) {
        return industry.name;
      }
    }

    return null;
  }

  /**
   * Verify that buttons are enabled when form is complete
   */
  async verifyButtonStates(): Promise<void> {
    const brandValue = await this.brandInput.inputValue();
    const selectedIndustry = await this.getSelectedIndustry();
    
    if (brandValue && selectedIndustry) {
      if (await this.startAnalysisButton.isVisible({ timeout: Timeouts.SHORT })) {
        const isDisabled = await this.startAnalysisButton.isDisabled();
        expect(isDisabled).toBe(false);
      }
    }
  }

  /**
   * Check for validation messages
   */
  async checkValidationMessages(): Promise<void> {
    const errorMessages = await this.page.locator('.error, .validation-error, [role="alert"]')
      .allTextContents();
    
    // Should not have critical validation errors if form is properly filled
    const criticalErrors = errorMessages.filter(msg => 
      msg.toLowerCase().includes('required') || 
      msg.toLowerCase().includes('invalid')
    );
    
    expect(criticalErrors).toHaveLength(0);
  }
}