import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { images } = await request.json()
    
    // Mock response for local testing
    const descriptions = images.map(() => 
      Math.random() > 0.5 ? 'product' : 'avatar'
    )
    
    return NextResponse.json({
      success: true,
      descriptions,
      products: [
        {
          product_name: "Sample Product",
          product_type: "demo",
          brand_name: "Test Brand"
        }
      ],
      prompts: [
        "Professional product photography of Sample Product",
        "Lifestyle shot with Sample Product",
        "Creative advertisement for Sample Product"
      ],
      has_avatar: descriptions.includes('avatar')
    })
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Processing failed'
    }, { status: 500 })
  }
}