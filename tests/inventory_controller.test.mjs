// These exercise the shipped fetch controller; they are not browser/DOM tests.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';

const source = await readFile(new URL('../src/chineselearning/static/inventory.js', import.meta.url), 'utf8');
const {createInventoryController} = await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);
const result = (params, overrides = {}) => ({items: [{simplified: '学'}], total: 140,
    page: Number(params.get('page')), page_size: Number(params.get('page_size')),
    total_pages: 7, ...overrides});

test('controls request whole-result sorting/filtering and reset pagination', async () => {
    const calls = [];
    let rendered;
    const controller = createInventoryController({
        onChange: state => {rendered = state;},
        fetcher: async url => {
            const params = new URL(url, 'http://localhost').searchParams;
            calls.push(params);
            return {ok: true, json: async () => result(params)};
        },
    });
    await controller.load();
    assert.equal(calls.at(-1).get('hsk_scheme'), 'newest');
    assert.equal(calls.at(-1).get('page_size'), '20');
    await controller.navigate(1);
    assert.equal(rendered.page, 2);
    await controller.filter('7');
    assert.equal(calls.at(-1).get('hsk_level'), '7');
    assert.equal(rendered.page, 1);
    await controller.navigate(1);
    await controller.resize(50);
    assert.equal(rendered.page, 1);
    assert.equal(calls.at(-1).get('page_size'), '50');
    await controller.navigate(1);
    await controller.sort('hsk_level');
    assert.equal(rendered.page, 1);
    assert.equal(calls.at(-1).get('sort'), 'hsk_level');
    assert.equal(calls.at(-1).get('order'), 'asc');
    await controller.sort('hsk_level');
    assert.equal(calls.at(-1).get('order'), 'desc');
    await controller.filter('');
    assert.equal(calls.at(-1).has('hsk_level'), false);
    const before = calls.length;
    await controller.navigate(-1);
    assert.equal(calls.length, before);
});

test('older responses and errors cannot replace a newer selection', async () => {
    const pending = [];
    let rendered;
    const controller = createInventoryController({onChange: state => {rendered = state;},
        fetcher: (url, options) => new Promise((resolve, reject) => pending.push({url, options, resolve, reject})),
    });
    const first = controller.load();
    const second = controller.filter('2');
    assert.equal(pending[0].options.signal.aborted, true);
    pending[1].resolve({ok: true, json: async () => ({items: [], total: 0, total_pages: 0})});
    await second;
    pending[0].resolve({ok: true, json: async () => ({items: [{simplified: '旧'}], total: 999})});
    await first;
    assert.equal(rendered.data.total, 0);
    const third = controller.load();
    const fourth = controller.filter('7');
    pending[3].resolve({ok: true, json: async () => ({items: [], total: 20, total_pages: 1})});
    await fourth;
    pending[2].reject(new Error('old request failed'));
    await third;
    assert.equal(rendered.error, null);
    assert.equal(rendered.data.total, 20);
    assert.equal(rendered.loading, false);
});

test('HTTP/network errors are visible state; retry and empty results recover', async () => {
    let rendered;
    let attempt = 0;
    const controller = createInventoryController({onChange: state => {rendered = state;},
        fetcher: async () => {
            attempt++;
            if (attempt === 1) return {ok: false, status: 503};
            if (attempt === 2) throw new Error('Network unavailable');
            return {ok: true, json: async () => ({items: [], total: 0, total_pages: 0})};
        },
    });
    const first = controller.load();
    assert.equal(rendered.loading, true);
    await first;
    assert.match(rendered.error, /503/);
    assert.equal(rendered.data, null);
    await controller.load();
    assert.equal(rendered.error, 'Network unavailable');
    await controller.load();
    assert.equal(rendered.error, null);
    assert.deepEqual(rendered.data.items, []);
    assert.equal(rendered.data.total, 0);
});
