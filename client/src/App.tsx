import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function App() {
  return (
    <div className='flex min-h-svh items-center justify-center bg-background'>
      <Card className='w-80'>
        <CardHeader>
          <CardTitle className='text-2xl font-bold'>EMS</CardTitle>
        </CardHeader>
        <CardContent>
          <Button>Funguje</Button>
        </CardContent>
      </Card>
    </div>
  );
}
