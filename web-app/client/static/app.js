console.log("test")


// Ajax request template
async function test_send_recv() {
    try {
        const response = await fetch('/test_send_recv_route', {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            }
        })

        if (!response.ok) {
            throw new Error('Network response was not ok')
        }

        const data = await response.json()
        console.log(JSON.stringify(data, null, 2))
    } catch (error) {
        console.error('Error:', error)
    }
}

test_send_recv()